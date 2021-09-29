from .preprocessor import PreprocessTransformation

TOURNAMENTS_PREPROCESS = [
    PreprocessTransformation("Tournament", "Tournament", "fill_na_with_value", ""),
    PreprocessTransformation("Location", "Location", "fill_na_with_value", ""),
    PreprocessTransformation("Series", "Series", "fill_na_with_value", ""),
    PreprocessTransformation("Court", "Court", "fill_na_with_value", ""),
    PreprocessTransformation("Surface", "Surface", "fill_na_with_value", ""),
    PreprocessTransformation("Date", "Date", "to_date"),
]

RESULTS_PREPROCESS = [
    PreprocessTransformation("Winner", "Winner", "fill_na_with_value", ""),
    PreprocessTransformation("Loser", "Loser", "fill_na_with_value", ""),
    PreprocessTransformation("Round", "Round", "fill_na_with_value", ""),
    PreprocessTransformation("Best of", "Best of", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("WRank", "WRank", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("LRank", "LRank", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("WPts", "WPts", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("LPts", "LPts", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("W1", "W1", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("L1", "L1", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("W2", "W2", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("L2", "L2", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("W3", "W3", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("L3", "L3", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("W4", "W4", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("L4", "L4", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("W5", "W5", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("L5", "L5", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("Wsets", "Wsets", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("Lsets", "Lsets", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("Comment", "Comment", "fill_na_with_value", ""),
]

BETS_PREPROCESS = [
    PreprocessTransformation("B365W", "B365W", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("B365L", "B365L", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("EXW", "EXW", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("EXL", "EXL", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("LBW", "LBW", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("LBL", "LBL", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("PSW", "PSW", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("PSL", "PSL", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("SJW", "SJW", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("SJL", "SJL", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("MaxW", "MaxW", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("MaxL", "MaxL", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("AvgW", "AvgW", "fill_na_and_negatives", 0, 0),
    PreprocessTransformation("AvgL", "AvgL", "fill_na_and_negatives", 0, 0),
]