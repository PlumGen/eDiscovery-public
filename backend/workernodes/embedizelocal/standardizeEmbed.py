

from collections import defaultdict

def standardizeEmbed(tokenizecomplete_list, engine, table_name_embed):

    model_to_hashes = {}
    all_model_hash_sets = []

    for MAINEMBEDMODEL in [i for i in tokenizecomplete_list if i != 'ALL']:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT DISTINCT row_hash
                FROM {table_name_embed}
                WHERE model_name = :model_name
            """), {"model_name": MAINEMBEDMODEL})
            row_hashes = set(row[0] for row in result)
            model_to_hashes[MAINEMBEDMODEL] = row_hashes
            all_model_hash_sets.append(row_hashes)

    # Intersection of all sets = row_hashes present in every model
    common_row_hashes = set.intersection(*all_model_hash_sets)


    with engine.connect() as conn:
        conn.execute(text(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = '{table_name_embed}'
                    AND column_name = 'in_all_models'
                ) THEN
                    ALTER TABLE {table_name_embed}
                    ADD COLUMN in_all_models INTEGER DEFAULT 0;
                END IF;
            END$$;
        """))
        conn.commit()

    with engine.begin() as conn:
        conn.execute(text(f"""
            UPDATE {table_name_embed}
            SET in_all_models = 0
        """))

    with engine.begin() as conn:
        conn.execute(
            text(f"""
                UPDATE {table_name_embed}
                SET in_all_models = 1
                WHERE row_hash = ANY(:hashes)
            """),
            {"hashes": list(common_row_hashes)}
        )
