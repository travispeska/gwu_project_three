pragma solidity ^0.5.0;

contract BloC2 {

    address operator;

    constructor() public {
        operator = msg.sender;
    }

    event Command(string data);

    modifier onlyOperator {
        require(msg.sender == operator, "You do not have permission to operate this malware!");
        _;
    }

    function issueCommand(string memory data) public onlyOperator {
        emit Command(data);
    }
}
