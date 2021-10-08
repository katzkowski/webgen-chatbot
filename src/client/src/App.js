import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import CloseIcon from "@mui/icons-material/Close";
import HelpIcon from "@mui/icons-material/Help";
import HomeIcon from "@mui/icons-material/Home";
import ImageIcon from "@mui/icons-material/Image";
import InfoIcon from "@mui/icons-material/Info";
import MenuIcon from "@mui/icons-material/Menu";
import {
  AppBar,
  Box,
  Button,
  Container,
  Fab,
  Grid,
  IconButton,
  SwipeableDrawer,
  Toolbar,
} from "@mui/material";
import Divider from "@mui/material/Divider";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import { useTheme } from "@mui/material/styles";
import Typography from "@mui/material/Typography";
import { styled } from "@mui/system";
import React, { useEffect, useRef, useState } from "react";
import { ColorModeContext } from "./AppWrapper";
import Chat from "./Chat";
import GeneratedImage from "./GeneratedImage";
import { SocketContext } from "./SocketProvider";

const drawerWidth = 240;

const Nav = styled("nav")(({ theme }) => ({
  [theme.breakpoints.up("md")]: {
    flexShrink: 0,
  },
}));

const Main = styled("main")(({ theme }) => ({
  flexGrow: 1,
  height: "100vh",
  overflow: "hidden",
}));

const StyledListItem = styled(ListItem)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius,
  minWidth: theme.spacing(6),
  textTransform: "uppercase",
  background: "none",
  px: theme.spacing(1),
  "&:hover": {
    background: theme.palette.grey[400],
  },
}));

const StyledListItemIcon = styled(ListItemIcon)(({ theme }) => ({
  minWidth: theme.spacing(5),
  color: "inherit",
}));

export default function App(props) {
  const { window } = props;
  const { context } = React.useContext(SocketContext);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [tab, setTab] = useState("home");
  const [input, setInput] = useState("");

  const inputRef = useRef(null);

  // set tab to generated on image update
  useEffect(() => {
    if (context.image !== null) {
      setTab("image");
    }
  }, [context.image, context.overlay]);

  const handleDrawerToggle = (open) => (event) => {
    if (
      event &&
      event.type === "keydown" &&
      (event.key === "Tab" || event.key === "Shift")
    ) {
      return;
    }

    setMobileOpen(open);
  };

  // theme
  const theme = useTheme();
  const colorMode = React.useContext(ColorModeContext);

  // container for drawer
  const container =
    window !== undefined ? () => window().document.body : undefined;

  // returns tabs depending on name
  const getTab = (name) => {
    if (name === "home") {
      return (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            height: "100%",
            justifyContent: "center",
          }}
        >
          <Typography variant="h3" sx={{ fontWeight: "900" }}>
            Create websites using natural language
          </Typography>
          <p>WebGen is a bot to create unique landing page designs.</p>
          <Box>
            <Button
              variant="contained"
              type="submit"
              onClick={() => {
                inputRef.current.value = "Create website";
                setInput("Create website");

                const inputForm = document.getElementById("input-form");
                // trigger submit event on form element around input
                inputForm.dispatchEvent(
                  new Event("submit", { cancelable: true, bubbles: true })
                );

                setTab("image");
              }}
            >
              Get started
            </Button>
          </Box>
        </Box>
      );
    } else if (name === "image") {
      return (
        <GeneratedImage>The generated image will appear here</GeneratedImage>
      );
    } else if (name === "about") {
      return <div>About tab</div>;
    } else {
      return <div>"undefined tab"</div>;
    }
  };

  // nav items
  const mainListItems = () => {
    return (
      <div>
        <StyledListItem
          button
          onClick={() => {
            setTab("home");
            setMenuOpen(false);
          }}
        >
          <StyledListItemIcon>
            <HomeIcon />
          </StyledListItemIcon>
          <ListItemText
            primary="Home"
            primaryTypographyProps={{ variant: "button" }}
          />
        </StyledListItem>
        <StyledListItem
          button
          onClick={() => {
            setTab("image");
            setMenuOpen(false);
          }}
        >
          <StyledListItemIcon>
            <ImageIcon />
          </StyledListItemIcon>
          <ListItemText
            primary="Generated"
            primaryTypographyProps={{ variant: "button" }}
          />
        </StyledListItem>
        <StyledListItem
          button
          onClick={() => {
            setTab("about");
            setMenuOpen(false);
          }}
        >
          <StyledListItemIcon>
            <InfoIcon />
          </StyledListItemIcon>
          <ListItemText
            primary="About"
            primaryTypographyProps={{ variant: "button" }}
          />
        </StyledListItem>
        <StyledListItem
          button
          onClick={() => {
            setTab("help");
            setMenuOpen(false);
          }}
        >
          <StyledListItemIcon>
            <HelpIcon />
          </StyledListItemIcon>
          <ListItemText
            primary="Help"
            primaryTypographyProps={{ variant: "button" }}
          />
        </StyledListItem>
      </div>
    );
  };

  // drawer content
  const drawer = (
    <Box>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          paddingLeft: theme.spacing(2),
          paddingRight: theme.spacing(1),
          ...theme.mixins.toolbar,
        }}
      >
        <Typography
          component="h1"
          variant="h5"
          color="inherit"
          noWrap
          sx={{ flexGrow: 1, my: 2 }}
        >
          WebGen
        </Typography>
      </Box>
      <Divider />
      <List>{mainListItems()}</List>
      <Divider />
      <List>
        <ListItem button>
          <ListItemIcon></ListItemIcon>
          <ListItemText primary="Legal" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box
      sx={{
        display: "flex",
        bgcolor: "background.default",
        position: "relative",
      }}
    >
      <AppBar
        position="fixed"
        elevation={1}
        sx={{
          display: {
            md: "None",
          },
          width: {
            md: `calc(100% - ${drawerWidth}px)`,
          },
          marginLeft: drawerWidth,
        }}
      >
        <Toolbar aria-label="menu" variant="dense">
          <IconButton
            edge="start"
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerToggle(true)}
            sx={{
              marginRight: theme.spacing(2),
              [theme.breakpoints.up("md")]: {
                display: "none",
              },
            }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            component="h1"
            variant="h6"
            color="inherit"
            noWrap
            sx={{ flexGrow: 1 }}
          >
            WebGen
          </Typography>
          <IconButton onClick={colorMode.toggleColorMode} color="inherit">
            {theme.palette.mode === "dark" ? (
              <Brightness7Icon />
            ) : (
              <Brightness4Icon />
            )}
          </IconButton>
        </Toolbar>
      </AppBar>
      <Nav
        sx={{
          position: "absolute",
          zIndex: "1500",
          top: theme.spacing(3),
          left: theme.spacing(3),
        }}
      >
        <Box
          sx={{
            display: { xs: "none", md: "flex" },
            flexDirection: "column",
            background: theme.palette.grey[300],
            borderRadius: 1,
            borderWidth: "1px",
            borderColor: theme.palette.grey[300],
            borderStyle: "solid",
            boxShadow: theme.shadows[6],
          }}
        >
          <Fab
            variant="extended"
            color="primiary"
            onClick={() => {
              setMenuOpen(!menuOpen);
            }}
            sx={{
              borderRadius: 1,
              minWidth: theme.spacing(15),
              boxShadow: "none",
              "&:hover": {
                background: theme.palette.grey[400],
              },
            }}
          >
            {menuOpen ? (
              <CloseIcon color="error" sx={{ mr: 1 }} />
            ) : (
              <MenuIcon sx={{ mr: 1 }} />
            )}
            {menuOpen ? "Close" : "Menu"}
          </Fab>
          <List
            sx={{
              display: menuOpen ? "block" : "none",
              pb: 0,
              zIndex: 1000,
              color: theme.palette.common.black,
            }}
          >
            {mainListItems()}
          </List>
        </Box>
        <SwipeableDrawer
          container={container}
          elevation={1}
          anchor={theme.direction === "rtl" ? "right" : "left"}
          open={mobileOpen}
          onOpen={handleDrawerToggle(true)}
          onClose={handleDrawerToggle(false)}
          sx={{
            flexShrink: 0,
            width: {
              xs: drawerWidth,
              md: 0,
            },
            "& .MuiDrawer-paper": {
              width: {
                xs: drawerWidth,
                md: 0,
              },
              boxSizing: "border-box",
            },
          }}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
        >
          {drawer}
        </SwipeableDrawer>
      </Nav>
      <Main>
        <Container
          maxWidth="lg"
          sx={{
            paddingTop: theme.spacing(4),
            paddingBottom: theme.spacing(4),
            height: "100%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            px: {
              xs: 0.5,
              md: 2.5,
            },
            py: {
              xs: 1,
              md: 2,
            },
          }}
        >
          <Grid container spacing={3} justifyContent="space-around">
            <Grid
              item
              md={6}
              sx={{
                display: {
                  xs: "None",
                  md: "block",
                },
              }}
            >
              {getTab(tab)}
            </Grid>
            <Grid item xs={12} md={6}>
              <Chat input={input} setInput={setInput} inputRef={inputRef} />
            </Grid>
          </Grid>
        </Container>
      </Main>
    </Box>
  );
}
