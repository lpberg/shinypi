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

	# Debug
    ui.accordion(
		ui.accordion_panel("Debug",
			ui.output_text_verbatim(id = "output_txt"),
		), open = False,
	),

	# Input Controlls
	ui.accordion(
		ui.accordion_panel("Filters",
			ui.layout_columns(
        		ui.output_ui("output_input_daterange"),
        		ui.output_ui("output_input_accounts"),
        		ui.output_ui("output_input_description"),
        		ui.output_ui("output_input_type"),
        		col_widths=(3,3),
    		),
		),
	),

	# Output

	# Tabs
	ui.navset_tab(
    	ui.nav_panel("Transactions",
			output_widget("plot_transactions"),
			ui.output_data_frame("table_transactions"),
		),
		ui.nav_panel("Monthly",
			ui.br(),
			ui.h5("Monthly spending by Description"),
			output_widget("plot_by_month"),
			ui.output_data_frame("table_monthly"),
		),
		ui.nav_panel("Montly Average",
			ui.br(),
			ui.h5("Monthly Average spending by Description"),
			output_widget("plot_by_month_ave"),
			ui.output_data_frame("table_monthly_ave"),

		),
		selected = "Transactions",
	),
	# App Theme
#	theme = shinyswatch.theme.zephyr,
)

def server(input, output, session):

	### Reactive Functions

	@reactive.calc
	def get_filtered_data():
		filtered_df = df
		filtered_df = filtered_df.loc[filtered_df['type'] == 'debit']
		filtered_df = filtered_df.loc[filtered_df['account'].isin(input.accounts())]
		start_date, end_date = input.daterange()
		filtered_df = filtered_df.loc[(filtered_df['date'].dt.date >= start_date) & (filtered_df['date'].dt.date < end_date)]
		filtered_df = filtered_df.loc[filtered_df['description'].isin(input.description())]
		filtered_df = filtered_df.loc[filtered_df['type'].isin(input.type())]
		return(filtered_df)

	@reactive.calc
	def get_monthly_data():
		df_grouped = get_filtered_data().groupby(['month_year','description','month_year_label'],observed=True,as_index=False).agg(
			total = pd.NamedAgg(column="amount",aggfunc="sum")
		)
		return(df_grouped)

	# Calcuate Monthly Average Group By Description
	@reactive.calc
	def get_monthly_description_ave():
		fdf = get_monthly_data().groupby(['description'],observed=True,as_index=False).agg(
			mean = pd.NamedAgg(column="total",aggfunc="mean")
		)
		fdf["mean"] = round(fdf["mean"],0)
		return(fdf)

	### Output

	@render.text
	def output_txt():
		return get_filtered_data().columns

	@render.data_frame
	def table_transactions():
		fdf = get_filtered_data()
		fdf = fdf[["date","description","amount","category"]]
		return(render.DataGrid(fdf,filters=True,width="100%"))

	@render.data_frame
	def table_monthly():
		fdf = get_monthly_data()[["description","total","month_year_label"]]
		fdf.sort_values('description', inplace=True)
		return render.DataGrid(
			fdf,
			filters=True,
			width="100%")

	@render.data_frame
	def table_monthly_ave():
		return render.DataGrid(
				get_monthly_description_ave(),
				filters=True,
				width="100%")

	@render_widget
	def plot_by_month_ave():
		return px.bar(
			data_frame = get_monthly_description_ave(),
			x = "description",
			y = "mean",
			text = "mean",
			color = "description"
			).update_layout(
				xaxis_title="Description",
				yaxis_title="Monthly Average ($)"
		)

	@render_widget
	def plot_by_month():
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
	def plot_transactions():
		return px.scatter(
			data_frame = get_filtered_data(),
			x="date",
			y="amount",
			color="description"
		).update_layout(
            xaxis_title="Date",
            yaxis_title="Amount ($)"
        )

	### UI Inputs 

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
					selected = ['Aldi','Target','Walmart'],
					multiple = True)

	# Type Input
	@render.ui
	def output_input_type():
		return ui.input_selectize("type", "Type:",
                    choices = list(df["type"].unique()),
                    selected = ['debit'],
                    multiple = True)

app = App(app_ui, server)

if __name__ == "__main__":
    run_app("app", host="0.0.0.0", port=8888, reload=True)
