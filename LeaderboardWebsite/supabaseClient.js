import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'

const SUPABASE_URL = 'https://zydpwkgiuhkwrqxokatb.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_Y9QENj5oiW1h7fIl67S14A_zRNV90Ot'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
export default supabase
