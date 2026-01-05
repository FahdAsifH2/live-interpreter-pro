-- Supabase Database Schema
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor)

-- Enable UUID extension (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create UserRole enum
DO $$ BEGIN
    CREATE TYPE userrole AS ENUM ('user', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create SubscriptionPlan enum
DO $$ BEGIN
    CREATE TYPE subscriptionplan AS ENUM ('free', 'basic', 'pro', 'enterprise');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create SubscriptionStatus enum
DO $$ BEGIN
    CREATE TYPE subscriptionstatus AS ENUM ('active', 'trial', 'cancelled', 'expired');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Users table
-- id is UUID from Supabase Auth, not SERIAL
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR,  -- Optional, Supabase Auth handles passwords
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    role userrole DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_id ON users(id);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan subscriptionplan DEFAULT 'free',
    status subscriptionstatus DEFAULT 'trial',
    stripe_subscription_id VARCHAR UNIQUE,
    stripe_customer_id VARCHAR,
    apple_transaction_id VARCHAR,
    google_purchase_token VARCHAR,
    trial_ends_at TIMESTAMP WITH TIME ZONE,
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_subscriptions_id ON subscriptions(id);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR,
    source_language VARCHAR NOT NULL,
    target_language VARCHAR NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_sessions_id ON sessions(id);
CREATE INDEX IF NOT EXISTS ix_sessions_user_id ON sessions(user_id);

-- Transcripts table
CREATE TABLE IF NOT EXISTS transcripts (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    translated_text TEXT,
    source_language VARCHAR NOT NULL,
    target_language VARCHAR NOT NULL,
    timestamp DOUBLE PRECISION NOT NULL,
    confidence DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_transcripts_id ON transcripts(id);
CREATE INDEX IF NOT EXISTS ix_transcripts_session_id ON transcripts(session_id);

-- Glossary entries table
CREATE TABLE IF NOT EXISTS glossary_entries (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_term VARCHAR NOT NULL,
    target_term VARCHAR NOT NULL,
    source_language VARCHAR NOT NULL,
    target_language VARCHAR NOT NULL,
    context TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_glossary_entries_id ON glossary_entries(id);
CREATE INDEX IF NOT EXISTS ix_glossary_entries_user_id ON glossary_entries(user_id);

-- Vocabulary entries table
CREATE TABLE IF NOT EXISTS vocabulary_entries (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word VARCHAR NOT NULL,
    translation VARCHAR NOT NULL,
    language VARCHAR NOT NULL,
    definition TEXT,
    example_sentence TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_vocabulary_entries_id ON vocabulary_entries(id);
CREATE INDEX IF NOT EXISTS ix_vocabulary_entries_user_id ON vocabulary_entries(user_id);

-- Enable Row Level Security (RLS) for Supabase Auth
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE glossary_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE vocabulary_entries ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for Supabase Auth
-- Users can view and update their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Sessions policies
CREATE POLICY "Users can manage own sessions" ON sessions
    FOR ALL USING (auth.uid() = user_id);

-- Transcripts policies
CREATE POLICY "Users can manage own transcripts" ON transcripts
    FOR ALL USING (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        )
    );

-- Glossary policies
CREATE POLICY "Users can manage own glossary" ON glossary_entries
    FOR ALL USING (auth.uid() = user_id);

-- Vocabulary policies
CREATE POLICY "Users can manage own vocabulary" ON vocabulary_entries
    FOR ALL USING (auth.uid() = user_id);

-- Subscriptions policies
CREATE POLICY "Users can manage own subscriptions" ON subscriptions
    FOR ALL USING (auth.uid() = user_id);

-- Note: Service role key bypasses RLS, so backend operations work normally
-- These policies protect direct database access from clients using anon key
