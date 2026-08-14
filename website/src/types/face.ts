import type { SkinColour } from "../enums/faceSkinColour";
import type { IrisColour } from "../enums/faceIrisColour";
import type { EyebrowStyle } from "../enums/faceEyebrowStyle";
import type { HairRelatedColour } from "./hairRelatedColour";

export interface Face {

    skinColourHeadRatio: {
        skinColour: SkinColour;
        headLength: number;
        headWidth: number;
        headDepth: number;
        faceHeight: number;
        faceSize: number;
    };

    eyes: {
        upperEyelidType: number;
        bottomEyelidType: number;
        eyeHeight: number;
        horizontalEyePosition: number;
        irisColour: IrisColour;
        pupilSize: number;
        upperEyelidHeightInner: number;
        upperEyelidWidthInner: number;
        upperEyelidHeightOuter: number;
        upperEyelidWidthOuter: number;
        innerEyeHeight: number;
        innerEyePosition: number;
        eyeCornerHeight: number;
        outerEyePosition: number;
        bottomEyelidHeight: number;
        eyeDepth: number;
    };

    foreheadBrows: {
        forehead: number;
        eyebrowType: number;
        eyebrowThickness: number;
        eyebrowStyle: EyebrowStyle;
        eyebrowDensity: number;
        eyebrowColour: HairRelatedColour;
        innerEyebrowHeight: number;
        browWidth: number;
        outerEyebrowHeight: number;
        templeWidth: number;
        eyebrowDepth: number;
    };

    nose: {
        noseType: number;
        laughterLines: number;
        noseHeight: number;
        nostrilWidth: number;
        noseWidth: number;
        noseTipDepth: number;
        noseDepth: number;
    };

    mouth: {
        upperLipType: number;
        lowerLipType: number;
        mouthHeight: number;
        lipSize: number;
        lipWidth: number;
        mouthCornerHeight: number;
        mouthDepth: number;
    };

    facialHair: {
        facialHairType: number;
        facialHairColour?: HairRelatedColour;
        thickness?: number;
    };

    cheeksChinJaw: {
        cheekType: number;
        neckLineType: number;
        cheekbones: number;
        chinHeight: number;
        chinWidth: number;
        jawHeight: number;
        jawline: number;
        chinDepth: number;
    };

    ears: {
        earLength: number;
        earWidth: number;
        earAngle: number;
    };

}