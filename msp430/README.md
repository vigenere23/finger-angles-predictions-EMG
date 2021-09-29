[⬅ BACK](../README.md)

# biomed-a21 - MSP-430

## Troubleshooting

### Opening the workspace

1. Open Code Composer Studio
2. Go to `File > Switch Workspace > Other...` and select `biomed-a21/msp430`.

**If projects do not appear** in the `Project Explorer` pane :

1. Go to `File > Import...`, select `CCS Projects`, click `Next >`
2. Browse to select `biomed-a21/msp430` (the entire workspace) as the search-directory, the select all 3 projects (`sender`, `receiver` and `shared`) to import them.

### Creating new project

1. Create it
    1. Go to `File > New > CCS Project`
    2. In `Target`, on the *right*, select `MSP430F5529`
    3. Give the project a name
    4. Make sure that the `Project type and tool-chain` is `Executable`
    5. Click `Finish`
2. Create the required folders
    1. Create a new folder named `src` where `.c` files will be placed
    2. Create a new folder named `include` where `.h` files will be placed
3. Change the project's settings
    1. Select the new project on the `Project Explorer` pane
    2. Go to `File > Properties`
    3. Go to `Build` and navigate to the `Dependencies` tab on the right. Click `Add...` and select the `shared` project.
    4. Go to `Build > MSP430 Compiler > Include Options`, double click on the `${PROJECT_ROOT}` entry and modify it to add the `/include` subfolder to the path.
    5. On the same page, also add the `shared/include` folder.
    6. Go to `Build > MSP430 Linker > File Search Path`. Click the add icon in the `Include library file o...` section, click `Workspace` and select `shared > Debug > shared.lib`.
        1. ⚠️**If the file does not exist, you will have to first build the project (to trigger the `shared` project build). Make sure to Save the settings before. If import error occurs, you can ignore them for now.**⚠️
    7. Apply changes and close
