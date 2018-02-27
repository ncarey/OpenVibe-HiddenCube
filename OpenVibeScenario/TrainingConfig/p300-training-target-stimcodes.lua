
-- this function is called when the box is initialized
function initialize(box)

	dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")

	stim0 = _G[box:get_setting(2)]
	stim1 = _G[box:get_setting(4)]
	
	launchTime = box:get_setting(3)
	
end

-- this function is called when the box is uninitialized
function uninitialize(box)
end

-- this function is called once by the box
function process(box)

	for i=1,10,1 do
		box:send_stimulation(1, stim0, launchTime, 0)
		box:send_stimulation(1, stim1, launchTime, 0)
		launchTime = launchTime + 5
	end
--	box:send_stimulation(1, stim1, launchTime, 0)

end
