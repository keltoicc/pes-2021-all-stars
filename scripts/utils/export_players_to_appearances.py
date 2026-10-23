from pathlib import Path
import csv


OUTPUT_FIELDS = """
Id;Name;PlayerId;Country;Version;FromSeason;ToSeason;PlayingStyle;POS;GK;CB;LB;RB;DMF;CMF;LMF;RMF;AMF;LWF;RWF;SS;CF;Overall;OffensiveAwareness;BallControl;Dribbling;TightPossession;LowPass;LoftedPass;Finishing;Heading;PlaceKicking;Curl;Speed;Acceleration;KickingPower;Jump;PhysicalContact;Balance;Stamina;DefensiveAwareness;BallWinning;Aggression;GKAwareness;GKCatching;GKClearing;GKReflexes;GKReach;WeakFootUsage;WeakFootAcc;Form;InjuryResistance;ScissorsFeint;DoubleTouch;FlipFlap;MarseilleTurn;Sombrero;CrossOverTurn;CutBehindAndTurn;ScotchMove;StepOnSkillcontrol;HeadingSpecial;LongRangeDrive;Chipshotcontrol;LongRangeShot;KnuckleShot;DippingShots;RisingShots;AcrobaticFinishing;HeelTrick;FirstTimeShot;OneTouchPass;ThroughPassing;WeightedPass;PinpointCrossing;OutsideCurler;Rabona;NoLookPass;LowLoftedPass;GKLowPunt;GKHighPunt;LongThrow;GKLongThrow;PenaltySpecialist;GKPenaltySaver;Gamesmanship;ManMarking;TrackBack;Interception;AcrobaticClear;Captaincy;SuperSub;FightingSpirit;Trickster;MazingRun;SpeedingBullet;IncisiveRun;LongBallExpert;EarlyCross;LongRanger;Weight;MarketValue;Reputation;Boots;Gloves;Shirt;ShirtNational;Overall-Style;Overall-Length;Overall-WaveLevel;Overall-HairVariation;Font-Style;Font-Parted;Font-Hairline;Font-ForeheadWidth;Side/Back-Style;Side/Back-Cropped;HairColourPreset;HairColourR;HairColourG;HairColourB;Accessory;AccessoryColour;SkinColour;HeadLength;HeadWidth;HeadDepth;FaceHeight;FaceSize;UpperEyelidType;BottomEyelidType;EyeHeight;HorizontalEyePosition;IrisColour;PupilSize;UpperEyelidHt.(Inner);UpperEyelidWd.(Inner);UpperEyelidHt.(Outer);UpperEyelidWd.(Outer);InnerEyeHeight;InnerEyePosition;EyeCornerHeight;OuterEyePosition;BottomEyelidHeight;EyeDepth;Forehead;EyebrowType;EyebrowThickness;EyebrowStyle;EyebrowDensity;EyebrowColourType;EyebrowColourR;EyebrowColourG;EyebrowColourB;InnerEyebrowHeight;BrowWidth;OuterEdyebrowHeight;TempleWidth;EyebrowDepth;NoseType;LaughterLines;NoseHeight;NostrilWidth;NoseWidth;NoseTipDepth;NoseDepth;UpperLipType;LowerLipType;MouthPosition;LipSize;LipWidth;MouthCornerHeight;MouthDepth;FacialHairType;FacialHairColourType;FacialHairColourR;FacialHairColourG;FacialHairColourB;Thickness;CheekType;NeckLineType;Cheekbones;ChinHeight;ChinWidth;JawHeight;Jawline;ChinDepth;EarLength;EarWidth;EarAngle;NeckLength;NeckSize;ShoulderHeight;ShoulderWidth;ChestMeasurement;WaistSize;ArmSize;ThighSize;CalfSize;LegLength;ArmLength
""".strip().split(";")


def get_first_line(value):
    if not value:
        return ""
    return value.splitlines()[0].strip()


def main():
    input_file = Path("config/evowebid/players.csv")
    output_file = Path("config/PlayerAppearances.csv")

    if not input_file.exists():
        print("No hay CSV de jugadores")
        return

    with input_file.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.DictReader(f, delimiter=";")

        with output_file.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as out:
            writer = csv.DictWriter(
                out,
                fieldnames=OUTPUT_FIELDS,
                delimiter=";",
                extrasaction="ignore",
            )

            writer.writeheader()

            for row in reader:
                player_id = row["Base ID:"].strip()

                if player_id == "0":
                    continue

                if row["Known as:"].strip():
                    name = row["Known as:"].strip()
                elif row["Full player name:"].strip():
                    name = row["Full player name:"].strip()
                else:
                    name = get_first_line(
                        row["Name (in-game):"]
                    )

                country = get_first_line(
                    row["Nationalities:"]
                )

                shirt = get_first_line(
                    row["Name on shirt:"]
                )

                shirt_national = get_first_line(
                    row["Name on shirt:"]
                )

                output_row = {
                    "Id": player_id,
                    "Name": name,
                    "Country": country,
                    "Shirt": shirt,
                    "ShirtNational": shirt_national,
                }

                writer.writerow(output_row)

    print(f"CSV generado correctamente: {output_file}")


if __name__ == "__main__":
    main()