from core_components.loops.library import AIAcquireTargetAction, EntityWaitAction, NoAction, WaitAction

game_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('entitywaitevent', EntityWaitAction()),
}

mob_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('entitywaitevent', EntityWaitAction()),
    ('aiacquiretargetevent', AIAcquireTargetAction()),  
}