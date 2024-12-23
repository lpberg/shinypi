from shiny import ui, render, App, run_app, reactive
from read_data_from_file import read_data

df = read_data()

# User Interface
app_ui = ui.page_fluid(
    ui.input_slider(id = "n", label = "N", min = 0, max = 100, value = 40),
    ui.output_text_verbatim(id = "output_txt"),
	ui.output_ui("output_input_accounts"),
	ui.output_table("output_result")
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
		filtered_df = filtered_df.loc[filtered_df['account'].isin(input.accounts())]
		return(filtered_df)
	@render.table
	def output_result():
		return(get_filtered_data())
	@render.ui
	def output_input_accounts():
		return ui.input_selectize("accounts", "Accounts:", choices=list(df["account"].unique()),multiple=True)

# This is a shiny.App object. It must be named `app`.
app = App(app_ui, server)

if __name__ == "__main__":
    run_app("app", host="0.0.0.0", port=8888, reload=True)
