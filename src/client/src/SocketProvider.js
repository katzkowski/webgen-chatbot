import React, { createContext, useEffect, useRef, useState } from "react";
import io from "socket.io-client";

export const socket = io("http://localhost:5000/");
export const SocketContext = createContext(null);
const messageQueue = [];
const minDuration = 750;

export const SocketProvider = (props) => {
  // application state
  const [state, _setState] = useState({
    sendingAllowed: false,
    lockAnimation: false,
    waiting: true,
    showTyping: false,
    setTypingAnimation: setTypingAnimation,
    messages: [],
    hints: [],
    image: null,
    spec: null,
    overlay: null,
    overlayScale: 100,
    color: null,
  });

  // ref to state
  const stateRef = useRef(state);

  // new setState method to use which updates stateRef and state
  // this is because event listeners need current state, using state freezes it for event listeners and they only use the state which was set during init.
  const setState = (newStateFunc) => {
    // ref expects object not function
    stateRef.current = newStateFunc();

    // pass function returing new state to "real" setState method
    _setState(() => {
      return stateRef.current;
    });
  };

  // setup sockets on component mount
  useEffect(() => {
    // allow sending messages on connection
    socket.on("connect", () => {
      setState(() => {
        return {
          ...stateRef.current,
          sendingAllowed: true,
        };
      });
    });

    // update overlay image
    socket.on("overlay", (data) => {
      if (data["url"] !== null) {
        setState(() => {
          return {
            ...stateRef.current,
            overlay: data.url,
          };
        });
      } else {
        setState(() => {
          return {
            ...stateRef.current,
            overlay: null,
          };
        });
      }
    });

    socket.on("message", (data) => {
      console.log("pushing data to queue: ", data);
      messageQueue.push({ data: data, type: "text" });
      console.log(messageQueue);

      // message received, set waiting = false
      setState(() => {
        return {
          ...stateRef.current,
          waiting: false,
        };
      });
    });

    socket.on("image", (data) => {
      console.log("received img");
      console.log("state: ", stateRef);

      const image = getImageUrl(data["image"]);
      const message = { data: { image: image }, type: "image" };

      messageQueue.push(message);
      console.log(messageQueue);

      // message received, set waiting = false
      setState(() => {
        return {
          ...stateRef.current,
          waiting: false,
        };
      });
    });
  }, []);

  useEffect(() => {
    console.log(
      `useEffect: lockAnimation = ${stateRef.current.lockAnimation}, waiting: ${stateRef.current.waiting}, queue length: ${messageQueue.length}`
    );
    // if currently not blocking and not waiting for messages
    if (!(stateRef.current.lockAnimation || stateRef.current.waiting)) {
      // hide animation
      setTypingAnimation(false);
      console.log("queue pop triggered");
      // process messages
      popMessageQueue();
    } else if (messageQueue.length !== 0) {
      setTimeout(() => {
        setState(() => {
          return {
            ...stateRef.current,
            waiting: false,
          };
        });
      }, minDuration);
    }
  }, [stateRef.current.lockAnimation, stateRef.current.waiting]);

  // blocking incoming messages after animation has been shown
  useEffect(() => {
    if (stateRef.current.showTyping) {
      setState(() => {
        return {
          ...stateRef.current,
          lockAnimation: true,
        };
      });
    }
  }, [state.showTyping]);

  // release animation lock after min duration
  useEffect(() => {
    if (stateRef.current.lockAnimation) {
      setTimeout(() => {
        setState(() => {
          return {
            ...stateRef.current,
            lockAnimation: false,
          };
        });
      }, minDuration);
    } else {
      // console.log("popping queue animation lock release");
      // popMessageQueue();
    }
  }, [state.lockAnimation]);

  /**
   * Handle an incoming message from the bot.
   * @param {Dict} data received from bot, including the message and optional images, specs, hints
   */
  const handleMessage = (payload) => {
    console.log(payload);
    const type = payload.type;
    let data = payload.data;

    // payload structure:
    // {data: {message: "msg", spec: obj, hints: [hint]}, type: "text"}
    // {data: {image: image, type: "image"}

    // extract hex value if specified
    const hex =
      "spec" in data &&
      data["spec"] &&
      "hex" in data["spec"] &&
      data["spec"]["hex"].length !== 0
        ? data["spec"]["hex"][0][2]
        : null;

    // extract overlay scale if specified
    let scale = null;
    try {
      if (data["spec"]["data"]["scale"] !== null) {
        scale = data["spec"]["data"]["scale"];
        console.log("setting scale to ", scale);
      }
    } catch (e) {
      // don't set scale
    }

    // clear hints, set new ones if specified
    let hints = [];
    if ("hints" in data) {
      hints = data["hints"];
    }

    // display table if image has been generated
    let spec = null;
    if (data["generate"]) {
      spec = data["spec"];
    }

    // extract message content
    if (type === "text") {
      data = data["message"];
    } else if (type === "image") {
      data = data["image"];
    }

    // append message to state from SocketContext.Provider
    setState(() => {
      return {
        ...stateRef.current,
        messages: [
          ...stateRef.current.messages,
          { data: data, isFromBot: true, type: type },
        ],
        color: hex,
        sendingAllowed: true,
        hints: hints,
        overlayScale: scale !== null ? scale : stateRef.current.overlayScale,
      };
    });

    if (spec !== null) {
      // push table to message state list
      setState(() => {
        return {
          ...stateRef.current,
          messages: [
            ...stateRef.current.messages,
            { data: spec, isFromBot: true, type: "table" },
          ],
        };
      });
    }
  };

  function setTypingAnimation(display) {
    if (display) {
      setState(() => {
        return {
          ...stateRef.current,
          showTyping: true,
        };
      });
    } else {
      setState(() => {
        return {
          ...stateRef.current,
          showTyping: false,
        };
      });
    }
  }

  function popMessageQueue(minDuration = 750) {
    // if a message has been received during typing animation
    if (messageQueue.length) {
      const data = messageQueue.shift();
      handleMessage(data);

      if ("image" in data.data) {
        const image = data.data.image;
        // append image to state from SocketContext.Provider
        setState(() => {
          return {
            ...stateRef.current,
            image: image,
            color: null, // reset color when new image is created
            overlay: null, // reset overlay when new image is created
            overlayScale: 100, // reset overlay scale
          };
        });
      }

      // recursively process messages until message queue is empty
      // wait for minDuration until showing animation again
      if (messageQueue.length !== 0) {
        setTimeout(() => {
          // wait for minDuration until processing next message
          // setState(() => {
          //   const newState = {
          //     lockAnimation: true,
          //     showTyping: true,
          //   };

          //   // merge old and new state
          //   return {
          //     ...stateRef.current,
          //     ...newState,
          //   };
          // });
          setTypingAnimation(true);
        }, minDuration);
      } else {
        console.log("empty message queue");
        setTimeout(() => {
          setState(() => {
            return {
              ...stateRef.current,
              waiting: true,
            };
          });
        }, minDuration);
      }
    }
  }

  const getImageUrl = (imageBytes) => {
    if (imageBytes) {
      // convert binary to jpeg
      const blob = new Blob([imageBytes], { type: "image/jpeg" });
      const urlCreator = window.URL || window.webkitURL;
      const imageUrl = urlCreator.createObjectURL(blob);

      return imageUrl;
    } else {
      return null;
    }
  };

  return (
    <SocketContext.Provider value={{ context: state, update: setState }}>
      {props.children}
    </SocketContext.Provider>
  );
};
