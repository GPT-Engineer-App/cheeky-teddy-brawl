import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { supabase } from '../lib/supabase';
import Battle from './Battle/Battle';
import Shop from './Shop';
import DailyChallenge from './DailyChallenge';
import BearEvolution from './BearEvolution';
import PlayerProfile from './PlayerProfile';
import LeaderboardComponent from './LeaderboardComponent';
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { captureEvent } from '../utils/posthog';
import { useSupabaseAuth } from '../hooks/useSupabaseAuth';
import Auth from './Auth';

const Game = () => {
  const [gameState, setGameState] = useState('menu');
  const [selectedTeddy, setSelectedTeddy] = useState(null);
  const { toast } = useToast();
  const { session } = useSupabaseAuth();

  const { data: playerTeddies, isLoading, error } = useQuery({
    queryKey: ['playerTeddies', session?.user?.id],
    queryFn: async () => {
      if (!session?.user) return null;
      const { data, error } = await supabase
        .from('player_teddies')
        .select('*, terrible_teddies(*)')
        .eq('player_id', session.user.id);
      if (error) throw error;
      return data.map(item => item.terrible_teddies);
    },
    enabled: !!session?.user,
  });

  useEffect(() => {
    if (playerTeddies && playerTeddies.length > 0) {
      setSelectedTeddy(playerTeddies[0]);
    }
  }, [playerTeddies]);

  const handleBattleEnd = (result) => {
    setGameState('menu');
    toast({
      title: result === 'win' ? "Victory!" : result === 'lose' ? "Defeat" : "Battle Ended",
      description: result === 'win' ? "You won the battle!" : result === 'lose' ? "You lost the battle." : "The battle has ended.",
      variant: result === 'win' ? "success" : result === 'lose' ? "destructive" : "default",
    });
    captureEvent('Battle_Ended', { result });
  };

  const startBattle = () => {
    if (!selectedTeddy) {
      toast({
        title: "Error",
        description: "Please select a teddy before starting a battle.",
        variant: "destructive",
      });
      return;
    }
    setGameState('battle');
    captureEvent('Battle_Started');
  };

  if (!session) {
    return <Auth />;
  }

  if (isLoading) return <div>Loading game...</div>;
  if (error) return <div>Error loading game data: {error.message}</div>;
  if (!playerTeddies) return <div>No teddies found. Please contact support.</div>;

  const renderGameContent = () => {
    switch (gameState) {
      case 'battle':
        return playerTeddies.length > 0 ? (
          <Battle
            playerTeddy={selectedTeddy}
            opponentTeddy={playerTeddies[Math.floor(Math.random() * playerTeddies.length)]}
            onBattleEnd={handleBattleEnd}
          />
        ) : (
          <div>Error: No teddies available for battle</div>
        );
      case 'shop':
        return <Shop />;
      case 'challenge':
        return <DailyChallenge />;
      case 'evolution':
        return selectedTeddy ? <BearEvolution teddy={selectedTeddy} /> : <div>Please select a teddy first.</div>;
      case 'profile':
        return <PlayerProfile />;
      case 'leaderboard':
        return <LeaderboardComponent />;
      default:
        return (
          <div className="menu flex flex-col space-y-4">
            <Button onClick={startBattle} disabled={!selectedTeddy}>Start Battle</Button>
            <Button onClick={() => {
              setGameState('shop');
              captureEvent('Shop_Opened');
            }}>Visit Shop</Button>
            <Button onClick={() => {
              setGameState('challenge');
              captureEvent('Daily_Challenge_Started');
            }}>Daily Challenge</Button>
            <Button onClick={() => {
              if (selectedTeddy) {
                setGameState('evolution');
                captureEvent('Evolution_Started');
              } else {
                toast({
                  title: "Error",
                  description: "Please select a teddy first.",
                  variant: "destructive",
                });
              }
            }}>Evolve Teddy</Button>
            <Button onClick={() => {
              setGameState('profile');
              captureEvent('Profile_Viewed');
            }}>View Profile</Button>
            <Button onClick={() => {
              setGameState('leaderboard');
              captureEvent('Leaderboard_Viewed');
            }}>Leaderboard</Button>
          </div>
        );
    }
  };

  return (
    <div className="game-container p-4 bg-gray-100 rounded-lg">
      <h1 className="text-3xl font-bold mb-4">Terrible Teddies</h1>
      {renderGameContent()}
      {gameState !== 'menu' && (
        <Button onClick={() => setGameState('menu')} className="mt-4">
          Back to Menu
        </Button>
      )}
    </div>
  );
};

export default Game;