# plyToDxf regional sorter

Script that transforms a single mesh defined in .ply to multiple individual .dxf files according to user defined sub-regions.

## Usage

- Follow the instructions given in the script.
- Make sure that the division nodes form a closed loop:
  - The division nodes are not order sensitive.
- Each sub-division is to be entered from outwards inwards, limbs first.
  - The sub-divisions are order-sensitive

Nodes and faces used in a sub-division will be removed from the original mesh. Think sequential.

## License
[MIT](https://choosealicense.com/licenses/mit/)
