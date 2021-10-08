import { useTheme } from "@emotion/react";
import {
  Box,
  styled,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Typography,
} from "@mui/material";
import React from "react";
import GeneratedImage from "./GeneratedImage";

const MessageContainer = styled(Box)(({ theme }) => ({
  maxWidth: "80%",
  padding: theme.spacing(1.5),
  margin: theme.spacing(1),
  borderRadius: theme.shape.borderRadius,
  color: theme.palette.text,
}));

export default function Message(props) {
  const theme = useTheme();

  // returns a table for a website spec object
  const createTable = (spec) => {
    let cat, feat;
    if ("cats" in spec) {
      // Dict[str, List[Tuple[str,str,str]]]
      cat = spec["cats"][0][2];
    }
    if ("feats" in spec) {
      feat = spec["feats"][0][2];
    }
    return (
      <TableContainer>
        <Table size="small">
          <TableBody>
            <TableRow
              sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
            >
              <TableCell>
                <Typography variant="button" component="span">
                  Category
                </Typography>
              </TableCell>

              <TableCell align="left">{cat}</TableCell>
            </TableRow>
            <TableRow
              sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
            >
              <TableCell>
                <Typography variant="button" component="span">
                  Features
                </Typography>
              </TableCell>
              <TableCell align="left">{feat}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  // renders the message according to its type: text, image or table
  const renderMessage = (payload) => {
    if (payload.type === "text") {
      return payload.data;
    } else if (payload.type === "table") {
      return createTable(payload.data);
    } else if (payload.type === "image") {
      return <GeneratedImage />;
    } else {
      return null;
    }
  };

  return (
    <Box>
      <MessageContainer
        sx={{
          float: props.bot ? "left" : "right",
          bgcolor: props.bot
            ? theme.palette.mode === "light"
              ? "grey.100"
              : "grey.800"
            : "primary.main",
          color: props.bot ? "text.primary" : "primary.contrastText",
          display: {
            xs: "block",
            md: props.type === "image" ? "none" : "block",
          },
          width: {
            xs: props.type === "image" ? "min(80%, 512px)" : "auto",
            md: "auto",
          },
        }}
      >
        {renderMessage(props.data)}
      </MessageContainer>
    </Box>
  );
}
