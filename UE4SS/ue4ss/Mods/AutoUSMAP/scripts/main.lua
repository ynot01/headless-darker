local done = false

local function do_dump()
    if done then return end
    done = true
    print("[AutoUSMAP] Generating Mappings.usmap ...")
    DumpUSMAP()
    print("[AutoUSMAP] Done. Check the UE4SS folder for Mappings.usmap.")
end

ExecuteInGameThread(function()
    do_dump()
end)
