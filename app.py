from shiny import ui, render, App, run_app, reactive
from read_data_from_file import read_data
import plotly.express as px
from shinywidgets import output_widget, render_widget
import pandas as pd

df = read_data()

# User Interface
app_ui = ui.page_fluid(

	ui.panel_title("ShinyPi"),

	ui.layout_columns(
		ui.output_ui("output_input_daterange"),
		ui.output_ui("output_input_accounts"),
		ui.output_ui("output_input_description"),
		col_widths=(3,3),
	),

    ui.output_text_verbatim(id = "output_txt"),

	ui.navset_tab(
    	ui.nav_panel("Table",
			ui.card(
				ui.output_table("output_result"),
			),
		),
    	ui.nav_panel("Scatter", 
			output_widget("scatter_plot"), 
		),
	)
)

# Server function
def server(input, output, session):
	@output

	@render.text
	def output_txt():
		return input.accounts()

	@reactive.calc
	def get_filtered_data():
		filtered_df = df
		# Filter by Type
		filtered_df = filtered_df.loc[filtered_df['type'] == 'debit']
		# Filter by Account
		filtered_df = filtered_df.loc[filtered_df['account'].isin(input.accounts())]
		# Filter by Date
		start_date, end_date = input.daterange()
		filtered_df = filtered_df.loc[(filtered_df['date'].dt.date >= start_date) & (filtered_df['date'].dt.date < end_date)]
		# Filter by Description
		filtered_df = filtered_df.loc[filtered_df['description'].isin(input.description())]
		return(filtered_df)

	@render.table
	def output_result():
		return(get_filtered_data())

	@render_widget
	def scatter_plot():
		return px.scatter(
			data_frame = get_filtered_data(),
			x="date",
			y="amount",
			color="description"
		)

	@render.ui
	def output_input_accounts():
		return ui.input_selectize("accounts", "Accounts:",
					choices = list(df["account"].unique()),
					selected = [account for account in df["account"].unique() if "Visa" in account],
					multiple = True)
	@render.ui
	def output_input_daterange():
		return ui.input_date_range("daterange","Dates:",
					start="2024-05-01",
			        end = "2024-10-10",
			        min = df["date"].min(),
			        max = df["date"].max(),
		)
	@render.ui
	def output_input_description():
		return ui.input_selectize("description", "Description:",
					choices = list(df["description"].unique()),
					selected = ['Costco','Target','Walmart'],
					multiple = True)

# This is a shiny.App object. It must be named `app`.
app = App(app_ui, server)

if __name__ == "__main__":
    run_app("app", host="0.0.0.0", port=8888, reload=True)
