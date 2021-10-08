import { Box, Button } from "@mui/material";
import React from "react";

export default function Hints(props) {
  return (
    <Box
      sx={{
        display: "flex",
        flexWrap: "wrap",
        marginLeft: 1,
        gap: 0.5,
      }}
    >
      {props.hints.map((hint, idx) => {
        return (
          <Button
            key={idx}
            onClick={props.onClick}
            variant="outlined"
            sx={{ mr: 0.5 }}
            data-hint={hint.replace(/^\w/, (c) => c.toUpperCase())}
          >
            {hint}
          </Button>
        );
      })}
    </Box>
  );
}
