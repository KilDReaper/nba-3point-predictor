from scripts.data_processing import load_dataset, harmonize_columns, clean_dataset

def main():
    raw = load_dataset('curry_2024_shots.csv')
    print('raw shape', raw.shape)
    h = harmonize_columns(raw)
    print('harmonized columns sample:', list(h.columns)[:12])
    if 'shotMade' in h.columns:
        print('harmonized shotMade counts:', h['shotMade'].value_counts(dropna=False).to_dict())
    else:
        print('harmonized shotMade not present')
    try:
        cleaned, report = clean_dataset(h)
        print('cleaned shape', cleaned.shape)
        print('cleaned shotMade counts:', cleaned['shotMade'].value_counts(dropna=False).to_dict())
    except Exception as e:
        print('clean_dataset error:', e)

if __name__ == '__main__':
    main()
