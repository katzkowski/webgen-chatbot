import { Box } from "@mui/material";
import { makeStyles } from "@mui/styles";

const useStyles = makeStyles((theme) => ({
  "@keyframes dotFlashing": {
    "0%": {
      backgroundColor: theme.palette.primary.main,
    },
    "50%": {},
    "100%": {
      backgroundColor: theme.palette.background.paper,
    },
  },
  dotFlashing: {
    position: "relative",
    marginLeft: theme.spacing(3),
    width: "10px",
    height: "10px",
    borderRadius: "5px",
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.main,
    animation: "$dotFlashing 1s infinite linear alternate",
    animationDelay: "0.5s",

    "&::before, &::after": {
      content: "''",
      display: "inline-block",
      position: "absolute",
      top: 0,
    },

    "&::before": {
      left: "-15px",
      width: "10px",
      height: "10px",
      borderRadius: "5px",
      backgroundColor: theme.palette.primary.main,
      color: theme.palette.primary.main,
      animation: "$dotFlashing 1s infinite alternate",
      animationDelay: "0s",
    },

    "&::after": {
      left: " 15px",
      width: "10px",
      height: "10px",
      borderRadius: "5px",
      backgroundColor: theme.palette.primary.main,
      color: theme.palette.primary.main,
      animation: "$dotFlashing 1s infinite alternate",
      animationDelay: "1s",
    },
  },
}));

export default function TypingIndicator({ visible }) {
  const classes = useStyles();

  return visible ? (
    <Box sx={{ m: 1 }}>
      <div className={`${classes.dotFlashing}`}></div>
    </Box>
  ) : null;
}
