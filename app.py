from shinywidgets import output_widget, render_widget
from shiny import ui, render, App, run_app, reactive
from read_data_from_file import read_data
import plotly.express as px
import pandas as pd
import shinyswatch

# Read data from file 
df = read_data()

# User Interface
app_ui = ui.page_fluid(
	# App Title
	ui.panel_title(ui.h2("ShinyPi")),
	# Input Controlls
	ui.layout_columns(
		ui.output_ui("output_input_daterange"),
		ui.output_ui("output_input_accounts"),
		ui.output_ui("output_input_description"),
		col_widths=(3,3),
	),
	# Output
    ui.output_text_verbatim(id = "output_txt"),
	# Tabs
	ui.navset_tab(
    	ui.nav_panel("Table",
			ui.card(
				ui.output_table("output_result"),
			),
		),
    	ui.nav_panel("Scatter",
			output_widget("scatter_plot"),
		),
		ui.nav_panel("Bar",
			ui.br(),
			ui.h5("Monthly spending by Description"),
			output_widget("bar_plot")
		),
		ui.nav_panel("Description",
			ui.br(),
			ui.h5("Monthly Average spending by Description"),
			output_widget("bar_plot_description")
		),
		selected = "Bar",
	),
	# App Theme
	theme = shinyswatch.theme.zephyr,
)

# Server function
def server(input, output, session):
	@output

	@render.text
	def output_txt():
		return get_monthly_data()

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

	@reactive.calc
	def get_monthly_data():
		df_filtered = get_filtered_data()
		df_grouped = df_filtered.groupby(['month_year','description','month_year_label'],observed=True,as_index=False).agg(
			total = pd.NamedAgg(column="amount",aggfunc="sum")
		)
		return(df_grouped)


	@render.table
	def output_result():
		return(get_monthly_data())

	@render_widget
	def bar_plot_description():
		df_filtered = get_monthly_data()
		df_grouped = df_filtered.groupby(['description'],observed=True,as_index=False).agg(
			mean = pd.NamedAgg(column="total",aggfunc="mean")
		)
		df_grouped["mean"] = round(df_grouped["mean"],0)
		return px.bar(
			data_frame = df_grouped,
			x = "description",
			y = "mean",
			text = "mean",
			color = "description"
			).update_layout(
				xaxis_title="Description",
				yaxis_title="Monthly Average ($)"
		)
	@render_widget
	def bar_plot():
		mydf = get_monthly_data()
		mydf.sort_values('month_year', inplace=True)
		mydf["total"] = round(mydf["total"],0)
		return px.bar(
			data_frame = mydf,
			x = "month_year_label",
			y = "total",
			text = "total",
			color = "description"
		).update_layout(
			xaxis_title="Month",
			yaxis_title="Total Amount ($)"
		)

	@render_widget
	def scatter_plot():
		return px.scatter(
			data_frame = get_filtered_data(),
			x="date",
			y="amount",
			color="description"
		).update_layout(
            xaxis_title="Date",
            yaxis_title="Amount ($)"
        )
	# Account Input
	@render.ui
	def output_input_accounts():
		return ui.input_selectize("accounts", "Accounts:",
					choices = list(df["account"].unique()),
					selected = [account for account in df["account"].unique() if "Visa" in account],
					multiple = True)
	# Date Range Input
	@render.ui
	def output_input_daterange():
		return ui.input_date_range("daterange","Dates:",
					start="2024-05-01",
			        end = "2024-10-10",
			        min = df["date"].min(),
			        max = df["date"].max(),
		)
	# Description Input
	@render.ui
	def output_input_description():
		return ui.input_selectize("description", "Description:",
					choices = list(df["description"].unique()),
					selected = ['Costco','Target','Walmart'],
					multiple = True)

# Create Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    run_app("app", host="0.0.0.0", port=8888, reload=True)
