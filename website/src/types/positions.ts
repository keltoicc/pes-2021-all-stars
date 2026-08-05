import type { Position } from "../enums/position";

export type PositionLevel = 1 | 2;

export type Positions = Partial<Record<Position, PositionLevel>>;