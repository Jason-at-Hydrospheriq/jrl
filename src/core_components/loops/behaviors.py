from core_components.loops.library import AIAcquireTargetAction, EntityWaitAction, KeyDownAction, NoAction, WaitAction

game_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('entitywaitevent', EntityWaitAction()),
    ('inputevent', KeyDownAction()),
}

mob_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('entitywaitevent', EntityWaitAction()),
    ('aiacquiretargetevent', AIAcquireTargetAction()),  
}