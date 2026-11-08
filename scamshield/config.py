from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
CLASSIC_PATH = BASE_DIR / "data" / "spam.csv"
INDIAN_TRAIN = BASE_DIR / "data" / "indian_train.csv"
INDIAN_TEST = BASE_DIR / "data" / "indian_test.csv"
KB_PATH = BASE_DIR / "data" / "knowledge_base.json"
MODEL_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
SEED = 42
TEST_SIZE = 0.30
ATTACK_SEEDS = 5
