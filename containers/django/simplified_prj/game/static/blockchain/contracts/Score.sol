// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract Score is Ownable {
    uint256 public counter = 1;

    mapping(uint256 => Game) public games;

    struct Game {
        string player1;
        string player2;
        uint8 player1Score;
        uint8 player2Score;
    }

	event GameSaved(string player1, string player2, uint8 player1Score, uint8 player2Score);
	//design pattern published subscribed
    constructor() Ownable(msg.sender) {}

    function saveGameScore(
        string calldata _player1,
        string calldata _player2,
        uint8 _player1Score,
        uint8 _player2Score
    ) external onlyOwner {
        games[counter] = Game(_player1, _player2, _player1Score, _player2Score);

        // Moins cher ++ à gauche
        ++counter;
		emit GameSaved(_player1, _player2, _player1Score, _player2Score);
    }

    //    Un-needed because of the public mapping
    //    function getGameInfo(uint256 gameId) external view returns (Game memory) {
    //        return games[gameId];
    //    }
}
