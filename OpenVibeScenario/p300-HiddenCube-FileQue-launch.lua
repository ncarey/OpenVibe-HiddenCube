-- well apparently we need this..
function sleep(n)
  if n > 0 then os.execute("ping -n " .. tonumber(n+1) .. " localhost > NUL") end
end

-- this function is called when the box is initialized
function initialize(box)

	dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")

	stim = _G[box:get_setting(2)]
	launchTime = box:get_setting(3)
	queFilename = box:get_setting(4)
end

-- this function is called when the box is uninitialized
function uninitialize(box)
end

-- this function is called once by the box
function process(box)
	while true do
		sleep(launchTime	)
		-- not sure if supposed to use : or .
		readyfile = io.open(queFilename, "r")
		isReady = readyfile.read()		
		readyfile:close()
		
		if isReady == "1" then
			readyfile = io.open(queFilename, "w")
			readyfile.writeline("0")
			readyfile:close()

			local now = box:get_current_time()
			box:send_stimulation(1, stim, now, 0)
		end
	end
end
