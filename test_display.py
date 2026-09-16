import unittest
from display_ui import select_view,title_lines,render_status
class DisplayTests(unittest.TestCase):
    def test_attention_priority_and_counts(self):
        tasks=[{'title':'Build','status':'Working','fresh':True},{'title':'Question','status':'Needs input','fresh':True},{'title':'Review','status':'Ready','fresh':True}]
        self.assertEqual(select_view({'connected':True,'tasks':tasks}),('input','Question',[1,1,1]))
    def test_stale_count_is_not_zero(self):
        tasks=[{'title':'Build','status':'Working','fresh':True},{'title':'Question','status':'Needs input','fresh':False}]
        self.assertEqual(select_view({'connected':True,'tasks':tasks}),('working','Build',None))
    def test_disconnect_overrides_stale_work(self):
        state={'connected':False,'tasks':[{'title':'Build','status':'Working','fresh':True}]}
        self.assertEqual(select_view(state)[0],'offline')
        self.assertIsNone(select_view(state)[2])
    def test_long_name_is_truncated_not_shrunk(self):
        lines=title_lines('An extremely long task name that cannot possibly fit into two lines without truncation')
        self.assertEqual(len(lines),2)
        self.assertTrue(lines[-1].endswith('...'))
    def test_all_states_have_device_sized_frames(self):
        for status in ['Working','Needs input','Ready','Idle','Failed','Unavailable']:
            im=render_status({'connected':True,'tasks':[{'title':'Test','status':status,'fresh':True}]})
            self.assertEqual((im.size,im.mode),((528,792),'1'))
if __name__=='__main__':unittest.main()
