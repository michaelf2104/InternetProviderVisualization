import logging
from tkinter import Tk, Label, StringVar, OptionMenu
from tkinterdnd2 import DND_FILES, TkinterDnD
from DataProcessor import DataProcessor
from HeatMapGenerator import HeatmapGenerator

# configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Application(TkinterDnD.Tk): 
    def __init__(self):
        super().__init__()
        
        self.previous_dataset_path = None  

        self.title("netzwerkanalyse")
        self.geometry("600x400")

        # available options for mnc and regions
        self.mnc_options = {
            "Telekom": [1, 6], 
            "Vodafone": [2, 4, 9],
            "Telefonica": [3, 5, 7, 8, 11, 77]
        }

        self.region_options = ["München", "Berlin", "Hamburg"]

        # create ui elements
        self.create_ui()

    def create_ui(self):
        label = Label(self, text="CSV-Datensatz bereitstellen")
        label.pack(pady=20)

        # drag and drop area for new dataset
        self.new_file_drop_area = Label(self, text="Datensatz", relief="solid", width=50, height=5)
        self.new_file_drop_area.pack(pady=10)

        # enable drag and drop for files
        self.new_file_drop_area.drop_target_register(DND_FILES)
        self.new_file_drop_area.dnd_bind('<<Drop>>', self.on_new_file_drop)

        # dropdown for mnc
        self.selected_mnc = StringVar(self)
        self.selected_mnc.set("Telekom")  # default value

        mnc_label = Label(self, text="Mobilfunkanbieter:")
        mnc_label.pack(pady=5)
        self.mnc_dropdown = OptionMenu(self, self.selected_mnc, *self.mnc_options.keys())
        self.mnc_dropdown.pack(pady=5)

        # dropdown for region
        self.selected_region = StringVar(self)
        self.selected_region.set("München")  # default value

        region_label = Label(self, text="Stadt:")
        region_label.pack(pady=5)
        self.region_dropdown = OptionMenu(self, self.selected_region, *self.region_options)
        self.region_dropdown.pack(pady=5)

    def on_old_file_drop(self, event):
        """
        stores the path of the old dataset
        """
        self.previous_dataset_path = event.data
        logger.info(f"old dataset received: {self.previous_dataset_path}")

    def on_new_file_drop(self, event):
        """
        processes the new dataset and generates heatmaps
        """
        new_dataset_path = event.data
        logger.info(f"new dataset received: {new_dataset_path}")

        # get selected region and mnc
        region = self.selected_region.get()
        mnc = self.mnc_options[self.selected_mnc.get()]

        # initialize data processor
        data_processor = DataProcessor(region_name=region, mnc=mnc, provider=self.selected_mnc)

        # process new dataset
        new_df = data_processor.load_and_clean_data(new_dataset_path)

        if self.previous_dataset_path:
            # compare with old dataset if available
            old_df = data_processor.load_and_clean_data(self.previous_dataset_path)
            new_data = data_processor.get_new_data(new_df, old_df)

            if new_data.empty:
                logger.info("no new data found. skipping heatmap generation.")
            else:
                self.generate_heatmaps(new_data)
        else:
            logger.warning("no previous dataset found. generating heatmaps for new dataset.")
            self.generate_heatmaps(new_df)

    def generate_heatmaps(self, df):
        """
        generates heatmaps for the given dataframe
        """
        heatmap_generator = HeatmapGenerator()
        heatmap_generator.generate_heatmap(df, "../heatmaps/new_heatmap.html")
        heatmap_generator.generate_circle_heatmap(df, "../heatmaps/new_circle_heatmap.html")
        logger.info("heatmaps generated successfully")

# start the gui application
if __name__ == "__main__":
    app = Application()
    app.mainloop()
