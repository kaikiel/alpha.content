# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s alpha.content -t test_company.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src alpha.content.testing.ALPHA_CONTENT_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/alpha/content/tests/robot/test_company.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Company
  Given a logged-in site administrator
    and an add Company form
   When I type 'My Company' into the title field
    and I submit the form
   Then a Company with the title 'My Company' has been created

Scenario: As a site administrator I can view a Company
  Given a logged-in site administrator
    and a Company 'My Company'
   When I go to the Company view
   Then I can see the Company title 'My Company'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Company form
  Go To  ${PLONE_URL}/++add++Company

a Company 'My Company'
  Create content  type=Company  id=my-company  title=My Company

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Company view
  Go To  ${PLONE_URL}/my-company
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Company with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Company title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
