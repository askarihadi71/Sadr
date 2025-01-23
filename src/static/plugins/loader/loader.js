function createLoader(count = 7, size, pading, animationSpeed = 6.4) {
    let loader = document.createElement('div')
    loader.classList.add('loader', 'loader1')
    loader.style.padding = pading
    loader.style.width = size
    loader.style.height = size

    let pervdiv = loader
    for (let i = 0; i < count; i++) {
        let newdiv = document.createElement('div')
        newdiv.style.padding = pading
        pervdiv.appendChild(newdiv)
        pervdiv = newdiv
    }
    loader.style = `padding: ${pading}; width: ${size}; height: ${size};animation:rotate linear ${animationSpeed}s infinite;`
    return loader
}

function createLoader25() {
    return createLoader(2, "25px", "2px", 1)
}

function createLoader50() {
    return createLoader(4, "50px", "2px", 1)
}

function createLoader85() {
    return createLoader(6, "85px", "4px", 1)
}

function createLoader100() {
    return createLoader(6, "100px", "5px", 1)
}

function createLoader150() {
    return createLoader(6, "150px", "8px")
}

function createLoader250() {
    return createLoader(8, "250px", "11px")
}