import type { SquadMember } from "../types/squadMember";
import type { PlayerVersion } from "../types/playerVersion";
import type { Player } from "../types/player";

export interface SquadMemberSummary {
    member: SquadMember;
    playerVersion: PlayerVersion;
    player: Player;
}