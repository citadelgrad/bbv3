"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface SearchFormProps {
  onSearch: (playerName: string) => void;
  isLoading: boolean;
}

export function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [playerName, setPlayerName] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (playerName.trim()) {
      onSearch(playerName.trim());
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-4 items-end">
      <div className="flex-1 space-y-2">
        <Label htmlFor="playerName">Player Name</Label>
        <Input
          id="playerName"
          type="text"
          placeholder="e.g., Juan Soto, Shohei Ohtani"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          disabled={isLoading}
          className="text-lg"
        />
      </div>
      <Button type="submit" size="lg" disabled={isLoading || !playerName.trim()}>
        {isLoading ? "Researching..." : "Research Player"}
      </Button>
    </form>
  );
}
