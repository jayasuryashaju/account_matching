

# Columns to be used from the input files
USE_COLUMNS = [ "Retailer Name", 'Item Description', "Distributor Name", "Street", "City", "State", "Zip code"]
DATABASE_COLUMNS = ['retailer_name', 'item_description', 'distributor_name', 'street', 'city', 'state', 'zip_code']


# Thresholds for scoring
HIGH_THRESHOLD = 0.9  # No Review Needed
LOW_THRESHOLD = 0.7  # Review Needed
