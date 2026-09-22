// Execute the instruction
String[] instructionParts_renamed = instruction.split(" ");
String opcode = instructionParts_renamed[0];
String operand1 = instructionParts_renamed[1];
String operand2 = instructionParts_renamed[2];

switch (opcode) {
    case "ADD":
        // Execute ADD instruction
        int operand1Value = register.readRegister(operand1);
        int operand2Value = register.readRegister(operand2);
        int result = operand1Value + operand2Value;
        register.writeRegister(operand1, result);
        break;
    case "SUB":
        // Execute SUB instruction
        operand1Value = register.readRegister(operand1);
        operand2Value = register.readRegister(operand2);
        result = operand1Value - operand2Value;
        register.writeRegister(operand1, result);
        break;
    case "JMP":
        // Execute JMP instruction
        String jumpAddress = operand1;
        instructionMemory.setPC(jumpAddress);
        break;
    default:
        // Handle unknown opcode
        System.out.println("Unknown opcode: " + opcode);
        break;
}

// Write back results to register bank
register.writeRegister("PC", address);
