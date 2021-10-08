import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { Box, FormControlLabel, IconButton, Menu, Switch } from "@mui/material";
import AppBar from "@mui/material/AppBar";
import CssBaseline from "@mui/material/CssBaseline";
import { useTheme } from "@mui/material/styles";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import useScrollTrigger from "@mui/material/useScrollTrigger";
import PropTypes from "prop-types";
import React from "react";
import { ColorModeContext } from "./AppWrapper";
import { socket } from "./SocketProvider";

function ElevationScroll(props) {
  const { children, window } = props;
  // Note that you normally won't need to set the window ref as useScrollTrigger
  // will default to window.
  // This is only being set here because the demo is in an iframe.
  const trigger = useScrollTrigger({
    disableHysteresis: true,
    threshold: 0,
    target: window ? window() : undefined,
  });

  return React.cloneElement(children, {
    elevation: trigger ? 4 : 0,
  });
}

ElevationScroll.propTypes = {
  children: PropTypes.element.isRequired,
  /**
   * Injected by the documentation to work in an iframe.
   * You won't need it on your project.
   */
  // window: PropTypes.func,
};

export default function ChatBar(props) {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [checked, setChecked] = React.useState(true);
  const open = Boolean(anchorEl);
  const theme = useTheme();
  const colorMode = React.useContext(ColorModeContext);

  const handleClick = (evt) => {
    setAnchorEl(evt.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  // toggle between generated and real images
  const handleVersionChange = (evt) => {
    setChecked(evt.target.checked);
    console.log("sending version event");
    socket.emit("version", { version: evt.target.checked });
  };

  return (
    <Box
      sx={{
        display: {
          xs: "None",
          md: "flex",
        },
      }}
    >
      <CssBaseline />
      <ElevationScroll {...props}>
        <AppBar
          position="relative"
          sx={{
            borderTopLeftRadius: theme.shape.borderRadius,
            borderTopRightRadius: theme.shape.borderRadius,
          }}
        >
          <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="h5">WebGen</Typography>
            <Box sx={{ display: "flex", pr: 0 }}>
              <IconButton onClick={colorMode.toggleColorMode} color="inherit">
                {theme.palette.mode === "dark" ? (
                  <Brightness7Icon />
                ) : (
                  <Brightness4Icon />
                )}
              </IconButton>
              <IconButton onClick={handleClick}>
                <MoreVertIcon sx={{ color: "common.white" }} />
              </IconButton>
              <Menu anchorEl={anchorEl} open={open} onClose={handleClose}>
                <FormControlLabel
                  control={
                    <Switch onChange={handleVersionChange} checked={checked} />
                  }
                  label="generated"
                  sx={{ px: 1, mr: 0.5 }}
                />
              </Menu>
            </Box>
          </Toolbar>
        </AppBar>
      </ElevationScroll>
    </Box>
  );
}
