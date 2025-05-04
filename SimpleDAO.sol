// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleDAO {
    struct Proposal {
        string description;
        uint256 votesYes;
        uint256 votesNo;
        bool executed;
    }

    address public owner;
    Proposal[] public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    function createProposal(string memory description) public onlyOwner {
        proposals.push(Proposal({
            description: description,
            votesYes: 0,
            votesNo: 0,
            executed: false
        }));
    }

    function vote(uint256 proposalId, bool support) public {
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        require(!proposals[proposalId].executed, "Already executed");

        hasVoted[proposalId][msg.sender] = true;

        if (support) {
            proposals[proposalId].votesYes++;
        } else {
            proposals[proposalId].votesNo++;
        }
    }

    function execute(uint256 proposalId) public onlyOwner {
        Proposal storage p = proposals[proposalId];
        require(!p.executed, "Already executed");
        require(p.votesYes > p.votesNo, "No majority");
        p.executed = true;
    }

    function getProposal(uint256 id) public view returns (
        string memory description,
        uint256 votesYes,
        uint256 votesNo,
        bool executed
    ) {
        Proposal storage p = proposals[id];
        return (p.description, p.votesYes, p.votesNo, p.executed);
    }

    function getProposalCount() public view returns (uint256) {
        return proposals.length;
    }
}
