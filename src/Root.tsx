import { Composition, Folder } from "remotion";
import { HelloWorld } from "./HelloWorld";
import { Main } from "./Edit/Main";
import { Natal, NATAL_DURATION } from "./Natal/Natal";
import { DURATION, FPS } from "./Edit/data";
import { Logo } from "./HelloWorld/Logo";
import { Trabalho, TRABALHO_DURATION } from "./Trabalho/Trabalho";
import { Title } from "./HelloWorld/Title";

// Each <Composition> is an entry in the sidebar!

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Trabalho" component={Trabalho} durationInFrames={TRABALHO_DURATION} fps={30} width={1080} height={1920} defaultProps={{ legenda: false }} />
      <Composition id="Natal" component={Natal} durationInFrames={NATAL_DURATION} fps={30} width={1080} height={1920} />
      <Composition
        id="Edit"
        component={Main}
        durationInFrames={Math.ceil(DURATION * FPS)}
        fps={FPS}
        width={1080}
        height={1920}
      />
      <Folder name="Elements">
        <Composition
          id="Logo"
          component={Logo}
          durationInFrames={150}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            logoColor1: "#91EAE4",
            logoColor2: "#86A8E7",
          }}
        />
        <Composition
          id="Title"
          component={Title}
          durationInFrames={115}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            titleText: "Welcome to Remotion",
            titleColor: "#000000",
          }}
        />
      </Folder>
      <Composition
        // You can take the "id" to render a video:
        // bunx remotion render HelloWorld
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        // You can override these props for each render:
        // https://www.remotion.dev/docs/parametrized-rendering
        defaultProps={{
          titleText: "Welcome to Remotion",
          titleColor: "#000000",
        }}
      />

    </>
  );
};
