## Logic flow

1. white canvas

2. lay the picture on top

3. crop it into a square using the minimum of width and height as the box length

4. grayscale the image

5. invert the image, so that the white pixels are the ones we wanna look at

6. upscale it so that it has a minimum resolution of 1000x1000 (using the scaling factor as `int(1000/box_length)+1`)

7. convert this image representation into an array

8. create a bordering circle of 'numPegs' number of pegs (user defined, maybe slider?)

   - the coordinates of the i<sup>th</sup> peg (x, y) are

        ```plaintext
        (((box_len/2)+(box_len/2)*cos(i*(360/numPegs))), (box_len/2)+(box_len/2)*sin(i*(360/numPegs)))
        ```

9. tell user to pick number of string passes (numPasses) (maybe a slider?)

10. check lines possible from starting peg to all other pegs, and pick line that has max brightness (this will have picked darkest line on the original image)

11. store the picked peg's index as the next starting peg, and the current peg's index as `previous_peg`

12. now decrement the value of pixels on that line by 1 in the stored array, by finding all coordinates of pixels that the line passes through

13. this means we have drawn the line as `RGBA(255, 255, 255, 1)` on the inverted image, but of course, we have technically asked to draw a faint black line `RGBA(0, 0, 0, 1)`

14. pick new peg and repeat the check as mentioned earlier
    > check lines possible from starting peg to all other pegs, and pick line that has max brightness (this will have picked darkest line on the original image)

15. avoid backtracking (maybe set a blacklist peg for every pass as the previous peg?) so it doesn't zip back and forth repeatedly, this means that the pegs checked, will not include the `previous_peg`

16. write the moves made to a file - cleaned-file-name_numPegs_numPasses

    1. cleaned-file-name means only `-` will be used to separate the words in the image filename, so that the file's name itself can be used to validate the number of moves specified and the max index of pegs used in the file

    2. the file itself will contain `numPasses` number of space-separated indexes, each containing the index of a peg.

17. make the moves specified, on a blank canvas object

18. _profit(?)_

## Folders

### img

will contain source images

### data

will contain the files that hold the drawing instructions (basically a space, comma or newline separated list of peg indexes)

### out

will contain the rendered outputs of performing each stage of source image processing and rendering
