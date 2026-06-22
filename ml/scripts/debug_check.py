from scripts.data_processing import load_dataset,harmonize_columns,clean_dataset
raw = load_dataset('curry_2024_shots.csv')
print('raw shape', raw.shape)

df = harmonize_columns(raw)
print('columns contains shotMade?', 'shotMade' in df.columns)

cleaned, report = clean_dataset(df)
print('clean shape', cleaned.shape)
print('shotMade value counts:\n', cleaned['shotMade'].value_counts(dropna=False).to_dict())
print('sample rows:\n', cleaned.head().to_string())
