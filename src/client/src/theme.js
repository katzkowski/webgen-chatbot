const common = {
  typography: {
    fontFamily: [
      "Inter",
      "-apple-system",
      "BlinkMacSystemFont",
      '"Segoe UI"',
      "Roboto",
      '"Helvetica Neue"',
      "Arial",
      "sans-serif",
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
    ].join(","),
  },
  shape: {
    borderRadius: 10,
  },
};

export const lightTheme = {
  ...common,
  ...{
    // palette: {
    //   primary: {
    //     light: "#56de83",
    //     main: "#00ab55",
    //     dark: "#007a29",
    //     contrastText: "#000000",
    //   },
    // },
  },
};

export const darkTheme = {
  ...common,
  ...{
    palette: {
      mode: "dark",
    },
    // background: {
    //   default: "#0a1929",
    // },
    // },
  },
};
