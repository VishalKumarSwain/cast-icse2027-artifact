def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting the job scraper...")
    gd = GlassdoorJobScraper()
    df = pd.read_csv("data/raw/joburls.csv")
    df = df[(df["job"] == "data engineer") & (df["MetroID"] >= 20)]
    for i, row in df.iterrows():
        gd.scrapeAndSaveAllJobDataFromURL(row)
