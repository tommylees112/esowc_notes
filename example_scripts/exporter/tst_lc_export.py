from pathlib import Path
import ftplib
import os
import string

from src.exporters.base import BaseExporter


class EsaCciExporter(BaseExporter):
    """Exports Land Cover Maps from ESA site

    ALL (55GB .nc)
    ftp://geo10.elie.ucl.ac.be/v207/ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992_2015-v2.0.7b.nc.zip

    YEARLY (300MB / yr .tif)

    LEGEND ( .csv)
    http://maps.elie.ucl.ac.be/CCI/viewer/download/ESACCI-LC-Legend.csv
    """

    def remove_punctuation(text: str):
        trans = str.maketrans("", "", string.punctuation)
        return text.lower().translate(trans)

    def read_legend():
        legend_url = (
            "http://maps.elie.ucl.ac.be/CCI/viewer/download/ESACCI-LC-Legend.csv"
        )
        df = pd.read_csv(legend_url, delimiter=";")
        df = df.rename(columns={"NB_LAB": "code", "LCCOwnLabel": "label"})

        # standardise text (remove punctuation & lowercase)
        df["label_text"] = df["label"].apply(remove_punctuation)
        df = df[["code", "label", "label_text", "R", "G", "B"]]

        return df

    def wget_file(self):
        url_path = (
            "ftp://geo10.elie.ucl.ac.be/v207/ESACCI-LC-L4"
            "-LCCS-Map-300m-P1Y-1992_2015-v2.0.7b.nc.zip".replace(" ", "")
        )
        os.system(f"wget {url_path} -P {self.landcover_folder.as_posix()}")

    def unzip(self):
        out_name = "ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992_2015-v2.0.7b.nc"
        fname = self.landcover_folder / (out_name + ".zip")
        assert fname.exists()
        print(f"Unzipping {fname.name}")

        os.system(f"unzip {fname.as_posix()}")
        print(f"{fname.name} unzipped!")

    def export(self) -> None:
        """Export functionality for the ESA CCI LandCover product
        """
        # write the download to landcover
        self.landcover_folder = self.raw_folder / "esa_cci_landcover"
        if not self.landcover_folder.exists():
            self.landcover_folder.mkdir()

        # check if the file already exists
        fname = "ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992_2015-v2.0.7b.nc.zip"
        if (self.landcover_folder / fname).exists():
            print("zip folder already exists. Unzipping")

        self.wget_file()


data_dir = Path("data")
e = EsaCciExporter(data_dir)
e.landcover_folder = e.raw_folder / "esa_cci_landcover"
e.unzip()
