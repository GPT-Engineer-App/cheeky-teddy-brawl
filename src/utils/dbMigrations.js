import { supabase } from '../lib/supabase';

const createMigrationFunction = `
CREATE OR REPLACE FUNCTION public.run_sql_migration(sql text)
RETURNS void AS $$
BEGIN
  EXECUTE sql;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
`;

const migrations = [
  `
  CREATE TABLE IF NOT EXISTS public.terrible_teddies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    special_move TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );
  `,
  `
  CREATE TABLE IF NOT EXISTS public.players (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    username TEXT UNIQUE NOT NULL,
    coins INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );
  `,
  `
  CREATE TABLE IF NOT EXISTS public.player_teddies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    player_id UUID REFERENCES public.players(id),
    teddy_id UUID REFERENCES public.terrible_teddies(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );
  `
];

export const runMigrations = async () => {
  console.log('Starting database migrations...');

  try {
    // Create the migration function
    const { error: functionError } = await supabase.rpc('run_sql_migration', { sql: createMigrationFunction });
    if (functionError) throw new Error(`Error creating migration function: ${functionError.message}`);
    console.log('Migration function created successfully');

    // Run migrations
    for (const [index, migration] of migrations.entries()) {
      const { error } = await supabase.rpc('run_sql_migration', { sql: migration });
      if (error) throw new Error(`Migration ${index + 1} error: ${error.message}`);
      console.log(`Executed migration ${index + 1}`);
    }

    console.log('Migrations completed successfully');
    return true;
  } catch (error) {
    console.error('Error during database migration:', error.message);
    throw error;
  }
};