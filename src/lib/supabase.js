import { createClient } from '@supabase/supabase-js';
import { runMigrations } from '../utils/dbMigrations';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export const initializeSupabase = async () => {
  try {
    const migrationsSuccessful = await runMigrations();
    
    if (!migrationsSuccessful) {
      throw new Error('Failed to run migrations');
    }
    
    const { data, error } = await supabase
      .from('terrible_teddies')
      .select('*')
      .limit(1);
    
    if (error) {
      console.error('Error fetching data:', error);
      throw new Error(`Failed to fetch data: ${error.message}`);
    }
    
    console.log('Supabase connection successful');
    return true;
  } catch (error) {
    console.error('Error initializing Supabase:', error.message);
    throw new Error(`Failed to initialize Supabase: ${error.message}`);
  }
};