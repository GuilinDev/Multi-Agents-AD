import { Composition } from "remotion";
import { PitchVideo } from "./PitchVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="PitchVideo"
      component={PitchVideo}
      durationInFrames={60 * 30} // 60 seconds at 30fps
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
