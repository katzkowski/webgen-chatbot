import SendIcon from "@mui/icons-material/Send";
import { Box, styled } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import React, { useContext } from "react";
import Hints from "./Hints";
import { socket, SocketContext } from "./SocketProvider";

const Form = styled("form")(({ theme }) => ({
  width: "100%",
  display: "flex",
  paddingLeft: theme.spacing(1),
  marginBottom: theme.spacing(1),
}));

export default function InputField(props) {
  // const classes = useStyles();
  const { context, update } = useContext(SocketContext);

  // send message to server via socket
  const handleSubmit = (msg) => {
    if (context.sendingAllowed && msg !== "" && msg.trim() !== "") {
      // send message
      socket.emit("message", { message: msg });

      // append user message to context state
      update(() => {
        return {
          ...context,
          sendingAllowed: false,
          waiting: true,
          messages: [
            ...context.messages,
            { data: msg, isFromBot: false, type: "text" },
          ],
        };
      });

      // clear input field
      props.setInput("");

      // show typing animation
      context.setTypingAnimation(true);
    }
  };

  const useHint = (evt) => {
    // get capitalized data tag
    props.inputRef.current.value = evt.target.dataset.hint;
    handleSubmit(props.inputRef.current.value);
  };

  return (
    <Box>
      <Hints hints={context.hints} onClick={useHint} />
      <Form
        id="input-form"
        onSubmit={(evt) => {
          console.log(
            "submit triggered, current value: ",
            props.inputRef.current.value
          );
          evt.preventDefault();
          handleSubmit(props.inputRef.current.value);
        }}
      >
        <TextField
          inputRef={props.inputRef}
          placeholder="Message"
          variant="outlined"
          margin="dense"
          fullWidth
          value={props.input}
          size="small"
          onInput={(e) => props.setInput(e.target.value)}
        />
        <IconButton aria-label="send" type="submit" sx={{ py: 0, my: 0.75 }}>
          <SendIcon />
        </IconButton>
      </Form>
    </Box>
  );
}
