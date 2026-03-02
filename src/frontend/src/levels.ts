export type LevelDef = {
  level: number;
  scenarioId: number;
  title?: string;
};

export const LEVELS: LevelDef[] = [
  { level: 1, scenarioId: 1 },
  { level: 2, scenarioId: 1 },

  { level: 3, scenarioId: 2 },
  { level: 4, scenarioId: 2 },

  { level: 5, scenarioId: 3 },
  { level: 6, scenarioId: 3 },

  { level: 7, scenarioId: 4 },
  { level: 8, scenarioId: 4 },

  { level: 9, scenarioId: 5 },
  { level: 10, scenarioId: 5 },

  { level: 11, scenarioId: 6 },
  { level: 12, scenarioId: 7 },
  { level: 13, scenarioId: 8 },
  { level: 14, scenarioId: 9 },
  { level: 15, scenarioId: 6 },

  { level: 16, scenarioId: 6 },
  { level: 17, scenarioId: 7 },
  { level: 18, scenarioId: 8 },
  { level: 19, scenarioId: 9 },
  { level: 20, scenarioId: 6 },
];
