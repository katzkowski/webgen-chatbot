import { Box, CircularProgress, Paper } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import React, { useEffect, useRef } from "react";
import ChatBar from "./ChatBar";
import InputField from "./InputField";
import Message from "./Message";
import { SocketContext } from "./SocketProvider";
import TypingIndicator from "./TypingIndicator";

export default function Chat(props) {
  const theme = useTheme();
  const { context } = React.useContext(SocketContext);

  const chatRef = useRef(null);

  const scrollToBottom = () => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  };

  // scroll new messages and typing animation into view
  useEffect(scrollToBottom, [context.messages]);
  useEffect(scrollToBottom, [context.showTyping]);

  return (
    <Paper
      elevation={0}
      sx={{
        height: "calc(100vh - 48px)",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        border: {
          md: 1,
        },
        borderColor: {
          md: theme.palette.mode === "light" ? "grey.400" : "grey.700",
        },
        mt: {
          xs: 6,
          md: 0,
        },
      }}
    >
      <ChatBar flexGrow={5} />
      <Box
        ref={chatRef}
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 4,
          overflowY: "scroll",
          scrollBehavior: "smooth",
          "&::-webkit-scrollbar": {
            width: context.messages.length === 0 ? 0 : 7,
          },
          "&::-webkit-scrollbar-track": {
            boxShadow: "None",
          },
          "&::-webkit-scrollbar-thumb": {
            borderRadius: theme.shape.borderRadius,
            backgroundColor:
              theme.palette.mode === "light" ? "grey.400" : "grey.700",
            outlineWidth: "0px",
            outlineStyle: "solid",
            outlineColor:
              theme.palette.mode === "light" ? "grey.400" : "grey.700",
          },
        }}
      >
        {context.messages.map((data, idx) => {
          return (
            <Message
              bot={data.isFromBot}
              key={idx}
              type={data.type}
              data={data}
            />
          );
        })}
        {context.messages.length === 0 ? (
          <Box
            sx={{
              display: "flex",
              alignSelf: "center",
              height: "100%",
              alignItems: "center",
            }}
          >
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <CircularProgress />
              <Box sx={{ typography: "body1", my: 2 }}>
                Connecting to bot...
              </Box>
            </Box>
          </Box>
        ) : null}
        <TypingIndicator visible={context.showTyping} />
      </Box>
      <InputField
        input={props.input}
        setInput={props.setInput}
        inputRef={props.inputRef}
      />
    </Paper>
  );
}
