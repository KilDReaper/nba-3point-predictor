from pathlib import Path
import pandas as pd
import numpy as np

RAW_DIR = Path(__file__).resolve().parents[1] / 'data' / 'raw'
OUT_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_source():
    # prefer combined file if present
    candidates = [RAW_DIR / 'players_klay_lillard_2022-2024_shots.csv', Path('../curry_2024_shots.csv').resolve()]
    for p in candidates:
        if p.exists():
            return pd.read_csv(p)
    # fallback: use any *_shots.csv
    files = list(RAW_DIR.glob('*_shots.csv'))
    if files:
        return pd.read_csv(files[0])
    raise FileNotFoundError('No raw shots CSV found')


def synthesize_misses(df: pd.DataFrame, target_balance: float = 0.5, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    # Harmonize column name for target if present
    if 'SHOT_MADE_FLAG' in df.columns and 'shotMade' not in df.columns:
        df = df.rename(columns={'SHOT_MADE_FLAG': 'shotMade'})
    if 'shotMade' not in df.columns:
        # assume all made
        df['shotMade'] = 1

    made = df[df['shotMade'] == 1].copy()
    n_made = len(made)
    # determine number of misses to synthesize to reach desired balance
    desired_total = int(n_made / target_balance)
    n_misses = max(0, desired_total - n_made)

    if n_misses == 0:
        return df

    # sample rows to duplicate as misses
    choices = made.sample(n=n_misses, replace=True, random_state=random_state)
    synth = choices.copy()
    # perturb numeric location/distance slightly to simulate misses
    for col in ['SHOT_DISTANCE', 'shotDistance', 'LOC_X', 'LOC_Y', 'locationX', 'locationY']:
        if col in synth.columns:
            noise = rng.normal(loc=0, scale=max(1.0, synth[col].astype(float).std()*0.05), size=len(synth))
            synth[col] = pd.to_numeric(synth[col], errors='coerce').fillna(0) + noise

    # set target to 0
    if 'shotMade' in synth.columns:
        synth['shotMade'] = 0
    else:
        synth['SHOT_MADE_FLAG'] = 0

    combined = pd.concat([df, synth], ignore_index=True)
    return combined


def main():
    src = load_source()
    combined = synthesize_misses(src, target_balance=0.5, random_state=42)
    out = OUT_DIR / 'synthesized_balanced_shots.csv'
    combined.to_csv(out, index=False)
    print('Saved', out, 'rows', len(combined))
    if 'shotMade' in combined.columns:
        print('Counts:', combined['shotMade'].value_counts().to_dict())


if __name__ == '__main__':
    main()
