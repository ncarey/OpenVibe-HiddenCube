function wait_until(box, time)
	while box:get_current_time() < time do
		box:sleep()
	end
end

function wait_for(box, duration)
	wait_until(box, box:get_current_time() + duration)
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
		wait_for(box, launchTime)
		local readyfileR = assert(io.open(queFilename, "r"))
		local isReady = tonumber(readyfileR:read("*all"))		
		readyfileR:close()
		
		if isReady == 1 then
			local readyfileW = assert(io.open(queFilename, "w"))
			readyfileW:write("0")
			readyfileW:close()

			local now = box:get_current_time()
			box:send_stimulation(1, stim, now, 0)
		end
	end
end
