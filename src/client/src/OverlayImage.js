import { Box } from "@mui/material";
import React, { useRef } from "react";
import Draggable from "react-draggable";
import { SocketContext } from "./SocketProvider";

export default function OverlayImage() {
  const { context } = React.useContext(SocketContext);

  const nodeRef = useRef(null); // to avoid deprecated  ReactDOM.findDOMNode() error

  return (
    <Draggable
      nodeRef={nodeRef}
      bounds="parent"
      onMouseDown={(e) => e.preventDefault()}
    >
      <Box
        ref={nodeRef}
        sx={{
          zIndex: 1,
          position: "absolute",
          width: 200 * (context.overlayScale / 100) + "px",
          userDrag: "none",
          cursor: "move",
          height: "auto",
        }}
      >
        <img
          alt="overlay"
          src={context.overlay.link}
          style={{ width: "100%" }}
        />
      </Box>
    </Draggable>
  );
}
