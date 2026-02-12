import React from "react";
import { Button } from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";

const TeamsChatBot = () => {
  const handleClick = () => {
    alert("Teams bot is not configured yet.");
  };

  return (
    <Button
      variant="contained"
      color="primary"
      onClick={handleClick}
      sx={{
        position: "fixed",
        bottom: 20,
        right: 20,
        borderRadius: "50%",
        width: 60,
        height: 60,
        minWidth: 0,
        boxShadow: 3,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <ChatIcon />
    </Button>
  );
};

export default TeamsChatBot;
