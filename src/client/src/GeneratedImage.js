import { Box, Link, styled, Typography } from "@mui/material";
import React from "react";
import OverlayImage from "./OverlayImage";
import { SocketContext } from "./SocketProvider";

export const ImageContainer = styled(Box)(({ theme }) => ({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  overflow: "hidden",
  aspectRatio: "1",
  maxHeight: "512px",
  maxWidth: "512px",
  color: theme.palette.primary.contrastText,
  backgroundColor: theme.palette.primary.main,
  borderRadius: theme.shape.borderRadius,
  backgroundSize: "cover",
  position: "relative",
}));

export default function GeneratedImage() {
  const { context } = React.useContext(SocketContext);

  return (
    <Box
      style={{
        height: "100%",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
      }}
    >
      <ImageContainer
        sx={{
          position: "relative",
          "&::after": {
            content: "''",
            position: "absolute",
            width: "100%",
            height: "100%",
            backgroundSize: "100% 100%",
            backgroundImage:
              context.image !== null ? `url(${context.image})` : "none",
            opacity: context.image !== null ? 1 : 0,
            transition: "all 0.5s ease-in",
          },
        }}
      >
        {context.image !== null ? (
          <Box
            sx={{
              position: "relative",
              width: "100%",
              height: "100%",
              "&::before": {
                content: "''",
                zIndex: 1,
                position: "absolute",
                width: "100%",
                height: "100%",
                transition: "background 0.5s ease-in",
                mixBlendMode: "overlay",
                backgroundColor:
                  context.color !== null ? `${context.color}` : "none",
              },
            }}
          >
            {context.overlay !== null ? (
              <Box sx={{ position: "relative", width: "100%", height: "100%" }}>
                <Box
                  sx={{
                    position: "absolute",
                    zIndex: 2,
                    width: "100%",
                    height: "100%",
                  }}
                >
                  <OverlayImage />
                </Box>
              </Box>
            ) : null}
          </Box>
        ) : (
          "The generated website will appear here."
        )}
      </ImageContainer>
      {context.overlay !== null ? (
        <Typography variant="subtitle2">
          Overlay photo by{" "}
          <Link
            href={`https://unsplash.com/@${context.overlay.username}?utm_source=webgen-bot&utm_medium=referral`}
          >
            {context.overlay.user}
          </Link>{" "}
          on{" "}
          <Link href="https://unsplash.com/?utm_source=webgen-bot&utm_medium=referral">
            Unsplash
          </Link>
        </Typography>
      ) : null}
    </Box>
  );
}
